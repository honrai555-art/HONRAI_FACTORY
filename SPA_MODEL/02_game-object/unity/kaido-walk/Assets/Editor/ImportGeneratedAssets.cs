using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Text;
using UnityEditor;
using UnityEngine;

/// <summary>
/// blender/output_assets の glb/gltf を Assets/Generated へ搬入する Editor Script。
/// </summary>
public static class ImportGeneratedAssets
{
    private const string GeneratedAssetsDir = "Assets/Generated";
    private static readonly string[] SupportedExtensions = { ".glb", ".gltf" };
    private static readonly string[] RelatedExtensions = { ".bin", ".png", ".jpg", ".jpeg", ".webp" };

    [MenuItem("HONRAI/Import Generated Assets")]
    public static void RunFromMenu()
    {
        Run();
    }

    public static void Run()
    {
        var exitCode = 0;

        try
        {
            Log("=== Unity generated asset import started ===");

            var unityProjectRoot = GetUnityProjectRoot();
            var factoryRoot = GetFactoryRoot(unityProjectRoot);
            var sourceDir = Path.Combine(factoryRoot, "blender", "output_assets");
            var targetDir = Path.Combine(unityProjectRoot, GeneratedAssetsDir.Replace('/', Path.DirectorySeparatorChar));

            EnsureDirectory(targetDir);

            Log($"Factory root: {factoryRoot}");
            Log($"Source dir: {sourceDir}");
            Log($"Target dir: {targetDir}");

            if (!Directory.Exists(sourceDir))
            {
                LogWarning($"Source directory not found: {sourceDir}");
                SendDiscordNotification(Array.Empty<string>(), targetDir, factoryRoot);
                Log("=== Unity generated asset import complete (no source) ===");
                return;
            }

            var importedNames = ImportAssets(sourceDir, targetDir);
            AssetDatabase.Refresh();

            Log($"Imported {importedNames.Count} asset(s).");
            SendDiscordNotification(importedNames, targetDir, factoryRoot);
            Log("=== Unity generated asset import complete ===");
        }
        catch (Exception ex)
        {
            exitCode = 1;
            LogError(ex.ToString());
        }

        if (Application.isBatchMode)
        {
            EditorApplication.Exit(exitCode);
        }
        else if (exitCode != 0)
        {
            EditorUtility.DisplayDialog(
                "Import Generated Assets",
                "アセット搬入中にエラーが発生しました。logs/unity_import.log を確認してください。",
                "OK");
        }
    }

    private static List<string> ImportAssets(string sourceDir, string targetDir)
    {
        var importedNames = new List<string>();
        var sourceFiles = Directory.GetFiles(sourceDir);

        foreach (var sourcePath in sourceFiles)
        {
            var extension = Path.GetExtension(sourcePath).ToLowerInvariant();
            if (!IsSupportedAssetExtension(extension))
            {
                continue;
            }

            if (!ValidateAssetFile(sourcePath))
            {
                continue;
            }

            var fileName = Path.GetFileName(sourcePath);
            var targetPath = Path.Combine(targetDir, fileName);

            try
            {
                CopyWithRetry(sourcePath, targetPath);
                importedNames.Add(fileName);
                Log($"Imported: {fileName}");
                CopyRelatedFiles(sourceDir, targetDir, Path.GetFileNameWithoutExtension(fileName), importedNames);
            }
            catch (Exception ex)
            {
                LogError($"Failed to import '{fileName}': {ex.Message}");
            }
        }

        return importedNames;
    }

    private static void CopyRelatedFiles(
        string sourceDir,
        string targetDir,
        string baseName,
        List<string> importedNames)
    {
        foreach (var extension in RelatedExtensions)
        {
            var relatedSource = Path.Combine(sourceDir, baseName + extension);
            if (!File.Exists(relatedSource))
            {
                continue;
            }

            var relatedName = baseName + extension;
            var relatedTarget = Path.Combine(targetDir, relatedName);

            try
            {
                CopyWithRetry(relatedSource, relatedTarget);
                if (!importedNames.Contains(relatedName))
                {
                    importedNames.Add(relatedName);
                }

                Log($"Imported related file: {relatedName}");
            }
            catch (Exception ex)
            {
                LogWarning($"Failed to import related file '{relatedName}': {ex.Message}");
            }
        }
    }

    private static bool ValidateAssetFile(string sourcePath)
    {
        var fileName = Path.GetFileName(sourcePath);

        if (!File.Exists(sourcePath))
        {
            LogWarning($"Asset file missing: {fileName}");
            return false;
        }

        var fileInfo = new FileInfo(sourcePath);
        if (fileInfo.Length == 0)
        {
            LogError($"Asset file is empty (possible corruption): {fileName}");
            return false;
        }

        return true;
    }

    private static void CopyWithRetry(string sourcePath, string targetPath)
    {
        const int maxAttempts = 3;

        for (var attempt = 1; attempt <= maxAttempts; attempt++)
        {
            try
            {
                if (File.Exists(targetPath))
                {
                    Log($"Overwriting existing asset: {Path.GetFileName(targetPath)}");
                    File.SetAttributes(targetPath, FileAttributes.Normal);
                }

                File.Copy(sourcePath, targetPath, true);
                return;
            }
            catch (IOException ex) when (attempt < maxAttempts)
            {
                LogWarning(
                    $"File lock detected for '{Path.GetFileName(targetPath)}'. Retry {attempt}/{maxAttempts}: {ex.Message}");
                System.Threading.Thread.Sleep(500 * attempt);
            }
        }

        File.Copy(sourcePath, targetPath, true);
    }

    private static bool IsSupportedAssetExtension(string extension)
    {
        foreach (var supported in SupportedExtensions)
        {
            if (string.Equals(extension, supported, StringComparison.OrdinalIgnoreCase))
            {
                return true;
            }
        }

        return false;
    }

    private static void SendDiscordNotification(IReadOnlyList<string> importedNames, string targetDir, string factoryRoot)
    {
        if (string.Equals(Environment.GetEnvironmentVariable("HONRAI_SKIP_IMPORT_DISCORD"), "1", StringComparison.Ordinal))
        {
            Log("Discord notification skipped (delegated to blender pipeline).");
            return;
        }

        var webhookUrl = ResolveDiscordWebhookUrl(factoryRoot);
        if (string.IsNullOrWhiteSpace(webhookUrl))
        {
            LogWarning("DISCORD_WEBHOOK_URL is not set. Discord notification skipped.");
            return;
        }

        var message = new StringBuilder();
        message.AppendLine("generated assets imported");
        message.AppendLine($"imported count: {importedNames.Count}");

        if (importedNames.Count > 0)
        {
            message.AppendLine("asset names:");
            foreach (var name in importedNames)
            {
                message.AppendLine($"- {name}");
            }
        }
        else
        {
            message.AppendLine("asset names: (none)");
        }

        message.AppendLine($"generated path: {targetDir}");
        message.AppendLine($"date time: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");

        var payload = "{\"content\":" + JsonEscape(message.ToString()) + "}";
        PostJson(webhookUrl, payload);
        Log("Discord notification sent.");
    }

    private static void PostJson(string url, string jsonPayload)
    {
        var request = (HttpWebRequest)WebRequest.Create(url);
        request.Method = "POST";
        request.ContentType = "application/json";

        var bytes = Encoding.UTF8.GetBytes(jsonPayload);
        request.ContentLength = bytes.Length;

        using (var stream = request.GetRequestStream())
        {
            stream.Write(bytes, 0, bytes.Length);
        }

        using var response = (HttpWebResponse)request.GetResponse();
        if ((int)response.StatusCode >= 400)
        {
            throw new WebException($"Discord webhook failed: {(int)response.StatusCode} {response.StatusDescription}");
        }
    }

    private static string ResolveDiscordWebhookUrl(string factoryRoot)
    {
        var envUrl = Environment.GetEnvironmentVariable("DISCORD_WEBHOOK_URL");
        if (!string.IsNullOrWhiteSpace(envUrl))
        {
            return envUrl.Trim();
        }

        var botEnvPath = Path.Combine(factoryRoot, "bot", ".env");
        if (!File.Exists(botEnvPath))
        {
            return null;
        }

        foreach (var line in File.ReadAllLines(botEnvPath))
        {
            if (!line.StartsWith("DISCORD_WEBHOOK_URL=", StringComparison.Ordinal))
            {
                continue;
            }

            var value = line.Substring("DISCORD_WEBHOOK_URL=".Length).Trim();
            if (!string.IsNullOrWhiteSpace(value))
            {
                return value;
            }
        }

        return null;
    }

    private static string GetUnityProjectRoot()
    {
        return Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
    }

    private static string GetFactoryRoot(string unityProjectRoot)
    {
        var projectRootEnv = Environment.GetEnvironmentVariable("PROJECT_ROOT");
        if (!string.IsNullOrWhiteSpace(projectRootEnv) && Directory.Exists(projectRootEnv))
        {
            return Path.GetFullPath(projectRootEnv);
        }

        var candidate = Path.GetFullPath(Path.Combine(unityProjectRoot, "..", ".."));
        if (Directory.Exists(Path.Combine(candidate, "bot")) || Directory.Exists(Path.Combine(candidate, "scripts")))
        {
            return candidate;
        }

        return unityProjectRoot;
    }

    private static void EnsureDirectory(string path)
    {
        if (!Directory.Exists(path))
        {
            Directory.CreateDirectory(path);
        }
    }

    private static string JsonEscape(string value)
    {
        if (value == null)
        {
            return "\"\"";
        }

        var escaped = value
            .Replace("\\", "\\\\")
            .Replace("\"", "\\\"")
            .Replace("\r", "\\r")
            .Replace("\n", "\\n");
        return $"\"{escaped}\"";
    }

    private static void Log(string message)
    {
        WriteLog("INFO", message);
        Debug.Log($"[ImportGeneratedAssets] {message}");
    }

    private static void LogWarning(string message)
    {
        WriteLog("WARN", message);
        Debug.LogWarning($"[ImportGeneratedAssets] {message}");
    }

    private static void LogError(string message)
    {
        WriteLog("ERROR", message);
        Debug.LogError($"[ImportGeneratedAssets] {message}");
    }

    private static void WriteLog(string level, string message)
    {
        try
        {
            var unityProjectRoot = GetUnityProjectRoot();
            var factoryRoot = GetFactoryRoot(unityProjectRoot);
            var logsDir = Path.Combine(factoryRoot, "logs");
            if (!Directory.Exists(logsDir))
            {
                Directory.CreateDirectory(logsDir);
            }

            var logPath = Path.Combine(logsDir, "unity_import.log");
            var line = $"{DateTime.Now:yyyy-MM-dd HH:mm:ss} [{level}] {message}{Environment.NewLine}";
            File.AppendAllText(logPath, line, Encoding.UTF8);
        }
        catch (Exception ex)
        {
            Debug.LogError($"[ImportGeneratedAssets] Failed to write log file: {ex.Message}");
        }
    }
}
