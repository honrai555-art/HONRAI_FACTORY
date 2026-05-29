using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// world_request.json から最小限のゲーム空間を自動構築し、
/// プレビュー画像・ログ・Discord 通知を出力する Editor Script。
/// </summary>
public static class GenerateWorldFromJson
{
    private const string DefaultJson = @"{
  ""world_name"": ""KAIDO_FIRE_ROUTE"",
  ""theme"": ""火山の街道"",
  ""route_length"": 500,
  ""objects"": [""鳥居"", ""溶岩"", ""宿場町"", ""橋""],
  ""characters"": [""ホンライくん""],
  ""mood"": ""熱い・挑戦・敗者復活"",
  ""target"": ""Spatial軽量版""
}";

    // 本物 Prefab へ差し替えるときはここを更新する
    private static class PrefabPaths
    {
        public const string Torii = "Assets/Prefabs/World/Torii.prefab";
        public const string Lava = "Assets/Prefabs/World/Lava.prefab";
        public const string PostTown = "Assets/Prefabs/World/PostTown.prefab";
        public const string Bridge = "Assets/Prefabs/World/Bridge.prefab";
        public const string HonraiKun = "Assets/Prefabs/Characters/HonraiKun.prefab";
    }

    private const string GeneratedAssetsDir = "Assets/Generated";

    private static readonly Dictionary<string, string> ObjectSlugMap = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
    {
        { "鳥居", "torii" },
        { "torii", "torii" },
        { "橋", "bridge" },
        { "bridge", "bridge" },
        { "溶岩", "lava" },
        { "lava", "lava" },
        { "lava_rock", "lava_rock" },
        { "宿場町", "post_town" },
        { "posttown", "post_town" },
        { "post_town", "post_town" },
        { "森", "forest" },
        { "forest", "forest" },
        { "川", "river" },
        { "river", "river" },
        { "山", "mountain" },
        { "mountain", "mountain" },
        { "神社", "shrine" },
        { "shrine", "shrine" },
        { "火山", "volcano" },
        { "volcano", "volcano" },
        { "ホンライくん", "honrai_kun" },
        { "honrai_kun", "honrai_kun" },
    };

    [Serializable]
    private class WorldRequest
    {
        public string world_name = "KAIDO_FIRE_ROUTE";
        public string theme = "火山の街道";
        public int route_length = 500;
        public string[] objects = Array.Empty<string>();
        public string[] characters = Array.Empty<string>();
        public string mood = "";
        public string target = "Spatial軽量版";
    }

    [MenuItem("HONRAI/Generate World From JSON")]
    public static void RunFromMenu()
    {
        Run();
    }

    public static void Run()
    {
        var exitCode = 0;

        try
        {
            Log("=== Unity world build started ===");

            var unityProjectRoot = GetUnityProjectRoot();
            var factoryRoot = GetFactoryRoot(unityProjectRoot);
            var jsonPath = ResolveJsonPath(unityProjectRoot, factoryRoot);
            var logPath = EnsureDirectory(Path.Combine(factoryRoot, "logs")) + "unity_world_build.log";
            var previewDir = EnsureDirectory(Path.Combine(factoryRoot, "BuildPreviews"));
            var previewPath = Path.Combine(previewDir, "preview.png");

            Log($"Unity project root: {unityProjectRoot}");
            Log($"Factory root: {factoryRoot}");
            Log($"JSON path: {jsonPath}");
            Log($"Log path: {logPath}");
            Log($"Preview path: {previewPath}");

            var request = LoadOrCreateRequest(jsonPath);
            Log($"Loaded world request: {request.world_name} / {request.theme}");

            var scene = BuildWorld(request);
            SaveScene(scene, request.world_name);

            var previewCamera = SetupPreviewCamera(request.route_length);
            CapturePreview(previewCamera, previewPath);
            Log($"Preview saved: {previewPath}");

            SendDiscordNotification(request, previewPath, factoryRoot);

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Log("=== Unity world build complete ===");
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
                "Generate World From JSON",
                "ワールド生成中にエラーが発生しました。logs/unity_world_build.log を確認してください。",
                "OK");
        }
    }

    private static WorldRequest LoadOrCreateRequest(string jsonPath)
    {
        if (!File.Exists(jsonPath))
        {
            LogWarning($"world_request.json not found. Creating default at: {jsonPath}");
            File.WriteAllText(jsonPath, DefaultJson, new UTF8Encoding(false));
            AssetDatabase.Refresh();
        }

        var json = File.ReadAllText(jsonPath, Encoding.UTF8);
        var request = JsonUtility.FromJson<WorldRequest>(json);
        if (request == null)
        {
            throw new InvalidDataException("world_request.json の解析に失敗しました。");
        }

        if (request.objects == null)
        {
            request.objects = Array.Empty<string>();
        }

        if (request.characters == null)
        {
            request.characters = Array.Empty<string>();
        }

        if (string.IsNullOrWhiteSpace(request.world_name))
        {
            request.world_name = "GeneratedWorld";
        }

        if (request.route_length <= 0)
        {
            request.route_length = 100;
        }

        return request;
    }

    private static Scene BuildWorld(WorldRequest request)
    {
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        var root = new GameObject("__WorldRoot__");

        CreateGround(root.transform, request.route_length);
        CreateRoute(root.transform, request.route_length);
        PlaceObjectsAlongRoute(root.transform, request);
        PlaceCharactersNearStart(root.transform, request);
        SetupLighting(root.transform);

        Log($"Scene built: {request.world_name}, route_length={request.route_length}");
        return scene;
    }

    private static void CreateGround(Transform parent, int routeLength)
    {
        var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "Ground";
        ground.transform.SetParent(parent, false);

        var width = Mathf.Max(20f, routeLength * 0.08f);
        var depth = Mathf.Max(30f, routeLength * 0.12f);
        ground.transform.localScale = new Vector3(width / 10f, 1f, depth / 10f);
        ground.transform.position = new Vector3(0f, 0f, routeLength * 0.5f);
        ApplyColor(ground, new Color(0.25f, 0.22f, 0.18f));
    }

    private static void CreateRoute(Transform parent, int routeLength)
    {
        var route = GameObject.CreatePrimitive(PrimitiveType.Cube);
        route.name = "Route";
        route.transform.SetParent(parent, false);
        route.transform.localScale = new Vector3(8f, 0.2f, routeLength);
        route.transform.position = new Vector3(0f, 0.11f, routeLength * 0.5f);
        ApplyColor(route, new Color(0.35f, 0.3f, 0.28f));
    }

    private static void PlaceObjectsAlongRoute(Transform parent, WorldRequest request)
    {
        if (request.objects.Length == 0)
        {
            return;
        }

        var spacing = Mathf.Max(20f, request.route_length / (float)(request.objects.Length + 1));
        var startOffset = Mathf.Max(15f, spacing);
        var characterBuffer = 12f;

        for (var i = 0; i < request.objects.Length; i++)
        {
            var objectName = request.objects[i];
            var z = startOffset + spacing * i;
            if (z < characterBuffer)
            {
                z = characterBuffer + spacing * 0.25f * i;
            }

            var side = (i % 2 == 0) ? -1f : 1f;
            var position = new Vector3(side * 6f, 0f, z);
            PlaceWorldObject(parent, objectName, position, i);
        }
    }

    private static void PlaceWorldObject(Transform parent, string objectName, Vector3 position, int index)
    {
        var generatedAsset = TryLoadGeneratedAsset(objectName);
        if (generatedAsset.Asset != null)
        {
            var instance = InstantiateGeneratedAsset(
                generatedAsset.Asset,
                parent,
                $"{objectName}_{index}",
                generatedAsset.Path);
            instance.transform.position = position;
            instance.transform.localScale = Vector3.one;
            instance.transform.rotation = Quaternion.Euler(0f, UnityEngine.Random.Range(-15f, 15f), 0f);
            Log($"Placed generated asset: {generatedAsset.Path} at {position}");
            return;
        }

        var prefab = TryLoadPrefab(objectName);
        if (prefab != null)
        {
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
            instance.name = $"{objectName}_{index}";
            instance.transform.position = position;
            instance.transform.localScale = Vector3.one;
            instance.transform.rotation = Quaternion.Euler(0f, UnityEngine.Random.Range(-15f, 15f), 0f);
            Log($"Placed prefab: {objectName} at {position}");
            return;
        }

        switch (objectName)
        {
            case "鳥居":
            case "torii":
                PlaceTorii(parent, position, index);
                break;
            case "溶岩":
            case "lava":
            case "lava_rock":
                PlaceLava(parent, position, index);
                break;
            case "宿場町":
            case "posttown":
            case "post_town":
                PlacePostTown(parent, position, index);
                break;
            case "橋":
            case "bridge":
                PlaceBridge(parent, position, index);
                break;
            default:
                PlaceFallbackCube(parent, objectName, position, index);
                break;
        }
    }

    private struct GeneratedAssetMatch
    {
        public GeneratedAssetMatch(GameObject asset, string path)
        {
            Asset = asset;
            Path = path;
        }

        public GameObject Asset { get; }
        public string Path { get; }
    }

    private static GeneratedAssetMatch TryLoadGeneratedAsset(string objectName)
    {
        foreach (var assetPath in BuildGeneratedAssetCandidates(objectName))
        {
            var asset = LoadImportedModel(assetPath);
            if (asset != null)
            {
                return new GeneratedAssetMatch(asset, assetPath);
            }
        }

        return new GeneratedAssetMatch(null, null);
    }

    private static IEnumerable<string> BuildGeneratedAssetCandidates(string objectName)
    {
        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var slug = ResolveObjectSlug(objectName);

        var names = new List<string> { slug, objectName, SanitizeFileName(objectName) };
        foreach (var name in names)
        {
            if (string.IsNullOrWhiteSpace(name) || !seen.Add(name))
            {
                continue;
            }

            yield return $"{GeneratedAssetsDir}/{name}.glb";
            yield return $"{GeneratedAssetsDir}/{name}.gltf";
        }
    }

    private static string ResolveObjectSlug(string objectName)
    {
        if (ObjectSlugMap.TryGetValue(objectName, out var slug))
        {
            return slug;
        }

        return SanitizeFileName(objectName).ToLowerInvariant();
    }

    private static GameObject LoadImportedModel(string assetPath)
    {
        var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(assetPath);
        if (prefab != null)
        {
            return prefab;
        }

        var assets = AssetDatabase.LoadAllAssetsAtPath(assetPath);
        foreach (var asset in assets)
        {
            if (asset is GameObject gameObject && gameObject.transform.parent == null)
            {
                return gameObject;
            }
        }

        return null;
    }

    private static GameObject InstantiateGeneratedAsset(
        GameObject asset,
        Transform parent,
        string instanceName,
        string assetPath)
    {
        GameObject instance = null;

        if (PrefabUtility.IsPartOfAnyPrefab(asset))
        {
            instance = (GameObject)PrefabUtility.InstantiatePrefab(asset, parent);
        }
        else
        {
            instance = UnityEngine.Object.Instantiate(asset, parent);
        }

        instance.name = instanceName;
        return instance;
    }

    private static GameObject TryLoadPrefab(string objectName)
    {
        var path = objectName switch
        {
            "鳥居" or "torii" => PrefabPaths.Torii,
            "溶岩" or "lava" => PrefabPaths.Lava,
            "宿場町" or "posttown" or "post_town" => PrefabPaths.PostTown,
            "橋" or "bridge" => PrefabPaths.Bridge,
            _ => null
        };

        if (string.IsNullOrEmpty(path))
        {
            return null;
        }

        return AssetDatabase.LoadAssetAtPath<GameObject>(path);
    }

    private static void PlaceTorii(Transform parent, Vector3 position, int index)
    {
        var toriiRoot = new GameObject($"Torii_{index}");
        toriiRoot.transform.SetParent(parent, false);
        toriiRoot.transform.position = position;

        CreateColoredCube(toriiRoot.transform, "Pillar_L", new Vector3(-1.5f, 2f, 0f), new Vector3(0.4f, 4f, 0.4f), Color.red);
        CreateColoredCube(toriiRoot.transform, "Pillar_R", new Vector3(1.5f, 2f, 0f), new Vector3(0.4f, 4f, 0.4f), Color.red);
        CreateColoredCube(toriiRoot.transform, "Lintel", new Vector3(0f, 3.8f, 0f), new Vector3(3.6f, 0.4f, 0.4f), new Color(0.85f, 0.1f, 0.1f));
    }

    private static void PlaceLava(Transform parent, Vector3 position, int index)
    {
        var lava = GameObject.CreatePrimitive(PrimitiveType.Cube);
        lava.name = $"Lava_{index}";
        lava.transform.SetParent(parent, false);
        lava.transform.position = position + new Vector3(0f, 0.15f, 0f);
        lava.transform.localScale = new Vector3(5f, 0.3f, 5f);
        ApplyColor(lava, new Color(0.9f, 0.2f, 0.05f));
    }

    private static void PlacePostTown(Transform parent, Vector3 position, int index)
    {
        var townRoot = new GameObject($"PostTown_{index}");
        townRoot.transform.SetParent(parent, false);
        townRoot.transform.position = position;

        var offsets = new[]
        {
            new Vector3(-2f, 1.5f, 0f),
            new Vector3(0f, 2f, 1.5f),
            new Vector3(2f, 1.2f, -1f),
            new Vector3(1f, 1.8f, 2f)
        };

        var scales = new[]
        {
            new Vector3(2f, 3f, 2f),
            new Vector3(2.5f, 4f, 2.5f),
            new Vector3(1.8f, 2.4f, 1.8f),
            new Vector3(2f, 3.6f, 2f)
        };

        for (var i = 0; i < offsets.Length; i++)
        {
            CreateColoredCube(
                townRoot.transform,
                $"Building_{i}",
                offsets[i],
                scales[i],
                new Color(0.55f, 0.45f, 0.35f));
        }
    }

    private static void PlaceBridge(Transform parent, Vector3 position, int index)
    {
        var bridge = GameObject.CreatePrimitive(PrimitiveType.Cube);
        bridge.name = $"Bridge_{index}";
        bridge.transform.SetParent(parent, false);
        bridge.transform.position = position + new Vector3(0f, 0.5f, 0f);
        bridge.transform.localScale = new Vector3(3f, 0.3f, 12f);
        ApplyColor(bridge, new Color(0.45f, 0.35f, 0.25f));
    }

    private static void PlaceFallbackCube(Transform parent, string objectName, Vector3 position, int index)
    {
        var cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
        cube.name = $"{objectName}_{index}";
        cube.transform.SetParent(parent, false);
        cube.transform.position = position + new Vector3(0f, 1f, 0f);
        cube.transform.localScale = Vector3.one * 2f;
        ApplyColor(cube, Color.gray);
        LogWarning($"Unknown object '{objectName}'. Placed fallback cube.");
    }

    private static void PlaceCharactersNearStart(Transform parent, WorldRequest request)
    {
        for (var i = 0; i < request.characters.Length; i++)
        {
            var characterName = request.characters[i];
            var position = new Vector3(-2f + i * 2f, 1f, 5f + i * 2f);
            PlaceCharacter(parent, characterName, position, i);
        }
    }

    private static void PlaceCharacter(Transform parent, string characterName, Vector3 position, int index)
    {
        var generatedAsset = TryLoadGeneratedAsset(characterName);
        if (generatedAsset.Asset != null)
        {
            var instance = InstantiateGeneratedAsset(
                generatedAsset.Asset,
                parent,
                $"{characterName}_{index}",
                generatedAsset.Path);
            instance.transform.position = position;
            instance.transform.localScale = Vector3.one;
            Log($"Placed generated character asset: {generatedAsset.Path}");
            return;
        }

        var prefabPath = characterName is "ホンライくん" or "honrai_kun" ? PrefabPaths.HonraiKun : null;
        if (!string.IsNullOrEmpty(prefabPath))
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
            if (prefab != null)
            {
                var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
                instance.name = $"{characterName}_{index}";
                instance.transform.position = position;
                Log($"Placed character prefab: {characterName}");
                return;
            }
        }

        if (characterName is "ホンライくん" or "honrai_kun")
        {
            var capsule = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            capsule.name = $"HonraiKun_{index}";
            capsule.transform.SetParent(parent, false);
            capsule.transform.position = position;
            ApplyColor(capsule, new Color(0.2f, 0.6f, 1f));
            return;
        }

        var fallback = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        fallback.name = $"{characterName}_{index}";
        fallback.transform.SetParent(parent, false);
        fallback.transform.position = position;
        ApplyColor(fallback, Color.cyan);
        LogWarning($"Unknown character '{characterName}'. Placed fallback capsule.");
    }

    private static void SetupLighting(Transform parent)
    {
        var lightGo = new GameObject("Directional Light");
        lightGo.transform.SetParent(parent, false);
        lightGo.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

        var light = lightGo.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.1f;
        light.color = new Color(1f, 0.95f, 0.85f);
    }

    private static Camera SetupPreviewCamera(int routeLength)
    {
        var cameraGo = new GameObject("Main Camera");
        var camera = cameraGo.AddComponent<Camera>();
        camera.tag = "MainCamera";
        camera.clearFlags = CameraClearFlags.Skybox;
        camera.fieldOfView = 60f;

        var focusZ = routeLength * 0.35f;
        cameraGo.transform.position = new Vector3(-25f, 30f, focusZ - 20f);
        cameraGo.transform.LookAt(new Vector3(0f, 0f, focusZ));

        return camera;
    }

    private static void SaveScene(Scene scene, string worldName)
    {
        var scenesDir = EnsureDirectory(Path.Combine(GetUnityProjectRoot(), "Assets", "Scenes"));
        var safeName = SanitizeFileName(worldName);
        var scenePath = Path.Combine(scenesDir, $"{safeName}.unity").Replace("\\", "/");

        if (!EditorSceneManager.SaveScene(scene, scenePath))
        {
            throw new IOException($"Scene の保存に失敗しました: {scenePath}");
        }

        Log($"Scene saved: {scenePath}");
    }

    private static void CapturePreview(Camera camera, string previewPath)
    {
        const int width = 1280;
        const int height = 720;

        var renderTexture = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
        var previousTarget = camera.targetTexture;
        var previousActive = RenderTexture.active;

        try
        {
            camera.targetTexture = renderTexture;
            camera.Render();

            RenderTexture.active = renderTexture;
            var texture = new Texture2D(width, height, TextureFormat.RGB24, false);
            texture.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            texture.Apply();

            var png = texture.EncodeToPNG();
            File.WriteAllBytes(previewPath, png);

            UnityEngine.Object.DestroyImmediate(texture);
        }
        finally
        {
            camera.targetTexture = previousTarget;
            RenderTexture.active = previousActive;
            renderTexture.Release();
            UnityEngine.Object.DestroyImmediate(renderTexture);
        }
    }

    private static void SendDiscordNotification(WorldRequest request, string previewPath, string factoryRoot)
    {
        var webhookUrl = ResolveDiscordWebhookUrl(factoryRoot);
        if (string.IsNullOrWhiteSpace(webhookUrl))
        {
            LogWarning("DISCORD_WEBHOOK_URL is not set. Discord notification skipped.");
            return;
        }

        var message = new StringBuilder();
        message.AppendLine("world build complete");
        message.AppendLine($"world_name: {request.world_name}");
        message.AppendLine($"theme: {request.theme}");
        message.AppendLine($"target: {request.target}");
        message.AppendLine($"preview path: {previewPath}");
        message.AppendLine($"date time: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");

        var payload = "{\"content\":" + JsonEscape(message.ToString()) + ",\"username\":\"HONRAI_FACTORY\"}";
        PostDiscord(webhookUrl, payload, previewPath);
        Log(File.Exists(previewPath) ? "Discord notification sent with preview image." : "Discord notification sent without preview image.");
    }

    private static void PostDiscord(string url, string jsonPayload, string previewPath)
    {
        if (!string.IsNullOrWhiteSpace(previewPath) && File.Exists(previewPath))
        {
            PostMultipart(url, jsonPayload, previewPath);
            return;
        }

        PostJson(url, jsonPayload);
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

    private static void PostMultipart(string url, string jsonPayload, string previewPath)
    {
        var boundary = "----HONRAI_FACTORY_" + Guid.NewGuid().ToString("N");
        var request = (HttpWebRequest)WebRequest.Create(url);
        request.Method = "POST";
        request.ContentType = "multipart/form-data; boundary=" + boundary;

        var fileName = Path.GetFileName(previewPath);
        var fileBytes = File.ReadAllBytes(previewPath);
        var header =
            $"--{boundary}\r\n" +
            "Content-Disposition: form-data; name=\"payload_json\"\r\n" +
            "Content-Type: application/json; charset=utf-8\r\n\r\n" +
            jsonPayload +
            "\r\n" +
            $"--{boundary}\r\n" +
            $"Content-Disposition: form-data; name=\"files[0]\"; filename=\"{fileName}\"\r\n" +
            "Content-Type: image/png\r\n\r\n";
        var footer = $"\r\n--{boundary}--\r\n";
        var headerBytes = Encoding.UTF8.GetBytes(header);
        var footerBytes = Encoding.UTF8.GetBytes(footer);
        request.ContentLength = headerBytes.Length + fileBytes.Length + footerBytes.Length;

        using (var stream = request.GetRequestStream())
        {
            stream.Write(headerBytes, 0, headerBytes.Length);
            stream.Write(fileBytes, 0, fileBytes.Length);
            stream.Write(footerBytes, 0, footerBytes.Length);
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

    private static string ResolveJsonPath(string unityProjectRoot, string factoryRoot)
    {
        var canonicalJson = Path.Combine(
            factoryRoot,
            "SPA_MODEL",
            "07_world-IP",
            "world-settings",
            "world_request.json");
        if (File.Exists(canonicalJson))
        {
            return canonicalJson;
        }

        var factoryJson = Path.Combine(factoryRoot, "world_request.json");
        if (File.Exists(factoryJson))
        {
            return factoryJson;
        }

        var projectJson = Path.Combine(unityProjectRoot, "world_request.json");
        if (File.Exists(projectJson))
        {
            return projectJson;
        }

        return canonicalJson;
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

    private static string EnsureDirectory(string path)
    {
        if (!Directory.Exists(path))
        {
            Directory.CreateDirectory(path);
        }

        return path.EndsWith(Path.DirectorySeparatorChar.ToString(), StringComparison.Ordinal)
            ? path
            : path + Path.DirectorySeparatorChar;
    }

    private static string SanitizeFileName(string name)
    {
        foreach (var invalid in Path.GetInvalidFileNameChars())
        {
            name = name.Replace(invalid, '_');
        }

        return string.IsNullOrWhiteSpace(name) ? "GeneratedWorld" : name;
    }

    private static void CreateColoredCube(
        Transform parent,
        string name,
        Vector3 localPosition,
        Vector3 localScale,
        Color color)
    {
        var cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
        cube.name = name;
        cube.transform.SetParent(parent, false);
        cube.transform.localPosition = localPosition;
        cube.transform.localScale = localScale;
        ApplyColor(cube, color);
    }

    private static void ApplyColor(GameObject target, Color color)
    {
        var renderer = target.GetComponent<Renderer>();
        if (renderer == null)
        {
            return;
        }

        var shader = Shader.Find("Standard");
        if (shader == null)
        {
            shader = Shader.Find("Universal Render Pipeline/Lit");
        }

        if (shader == null)
        {
            return;
        }

        var material = new Material(shader);
        if (material.HasProperty("_Color"))
        {
            material.color = color;
        }

        renderer.sharedMaterial = material;
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
        Debug.Log($"[GenerateWorldFromJson] {message}");
    }

    private static void LogWarning(string message)
    {
        WriteLog("WARN", message);
        Debug.LogWarning($"[GenerateWorldFromJson] {message}");
    }

    private static void LogError(string message)
    {
        WriteLog("ERROR", message);
        Debug.LogError($"[GenerateWorldFromJson] {message}");
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

            var logPath = Path.Combine(logsDir, "unity_world_build.log");
            var line = $"{DateTime.Now:yyyy-MM-dd HH:mm:ss} [{level}] {message}{Environment.NewLine}";
            File.AppendAllText(logPath, line, Encoding.UTF8);
        }
        catch (Exception ex)
        {
            Debug.LogError($"[GenerateWorldFromJson] Failed to write log file: {ex.Message}");
        }
    }
}
