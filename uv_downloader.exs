Mix.install([:httpoison])


defmodule OMI.Downloader do
  @moduledoc false

  require Logger
  alias HTTPoison.{AsyncResponse, AsyncStatus, AsyncHeaders, AsyncChunk, AsyncEnd, Error}

  @concurrency 4
  @recv_timeout 60_000

  def download_all(file_list, output_dir, token) do
    File.mkdir_p!(output_dir)
    headers = [{"Authorization", "Bearer #{token}"}]

    urls =
      File.read!(file_list)
      |> String.split(~r/\R/, trim: true)

    total = length(urls)

    urls
    |> Stream.with_index(1)
    |> Task.async_stream(
      fn {url, idx} -> {idx, download_one(url, headers, output_dir)} end,
      max_concurrency: @concurrency,
      timeout: :infinity
    )
    |> Enum.each(fn
      {:ok, {idx, {:ok, path}}} ->
        Logger.info("✅ Finished: #{idx}/#{total} #{Path.basename(path)}")

      {:ok, {idx, {:error, url, reason}}} ->
        Logger.error("❌ #{idx}/#{total} Failed #{url}: #{inspect(reason)}")

      {:exit, reason} ->
        Logger.error("💥 Task exited: #{inspect(reason)}")
    end)
    IO.puts("")
  end

  defp download_one("", _headers, _output_dir), do: {:ok, nil}
  defp download_one(url, headers, output_dir) do
    # filename =
    #   url
    #   |> URI.parse()
    #   |> Map.fetch!(:path)
    #   |> Path.basename()
    #   |> String.split("?")
    #   |> hd()

    filename = url |> URI.parse() |> Map.fetch!(:query) |> String.split("LABEL=") |> Enum.at(1) |> String.split("&") |> hd()

    file_path = Path.join(output_dir, filename)
    Logger.info("Starting #{filename}")

    File.open!(file_path, [:write, :binary], fn file ->
      case HTTPoison.get(url, headers, stream_to: self(), async: :once, recv_timeout: @recv_timeout) do
        {:ok, %AsyncResponse{} = resp} ->
          stream_chunks(resp, file)
          {:ok, file_path}

        {:error, %Error{reason: reason}} ->
          {:error, url, reason}
      end
    end)
  end

  defp stream_chunks(%AsyncResponse{id: ref} = resp, file) do
    receive do
      %AsyncStatus{id: ^ref, code: 200} ->
        HTTPoison.stream_next(resp)
        stream_chunks(resp, file)

      %AsyncHeaders{id: ^ref, headers: _hdrs} ->
        HTTPoison.stream_next(resp)
        stream_chunks(resp, file)

      %AsyncChunk{id: ^ref, chunk: chunk} ->
        IO.binwrite(file, chunk)
        HTTPoison.stream_next(resp)
        stream_chunks(resp, file)

      %AsyncEnd{id: ^ref} ->
        :ok
    after
      @recv_timeout ->
        raise "Timeout downloading ref #{inspect(ref)}"
    end
  end
end

# ─────────────── Script Entrypoint ─────────────── #

# 1) Hard-coded paths
file_list   = "./UV/subset_OMUVBd_003_20250612_112534_.txt"
output_dir  = "./UV/DIARIO/OMUVBd/DATA"
secret_file = "secret.py"

# 2) Read token from secret.py
secret_content = File.read!(secret_file)
[[_, token]]   = Regex.scan(~r/GIOVANNI_TOKEN\s*=\s*"(.*?)"/, secret_content)


# 3) Launch downloads
OMI.Downloader.download_all(file_list, output_dir, token)
