using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Minio;
using Minio.DataModel.Args;

namespace NuIeee.Application.Services.MinIO;

public class MinioService : IMinioService
{
    private readonly IMinioClient _minioClient;
    private readonly string _bucketName;
    private readonly ILogger<MinioService> _logger;

    public MinioService(IConfiguration configuration, ILogger<MinioService> logger)
    {
        _logger = logger;

        var minioConfig = configuration.GetSection("MinIO");
        var endpoint = minioConfig["Endpoint"] 
                       ?? throw new InvalidOperationException("MinIO Endpoint is not configured");
        var accessKey = minioConfig["AccessKey"] 
                        ?? throw new InvalidOperationException("MinIO AccessKey is not configured");
        var secretKey = minioConfig["SecretKey"] 
                        ?? throw new InvalidOperationException("MinIO SecretKey is not configured");
        _bucketName = minioConfig["BucketName"] 
                      ?? throw new InvalidOperationException("MinIO BucketName is not configured");
        var useSSL = bool.TryParse(minioConfig["UseSSL"], out var ssl) && ssl;

        _minioClient = new MinioClient()
            .WithEndpoint(endpoint)
            .WithCredentials(accessKey, secretKey)
            .WithSSL(useSSL)
            .Build();

        _logger.LogInformation("MinIO client initialized with endpoint: {Endpoint}, bucket: {BucketName}", endpoint, _bucketName);
    }

    public async Task<string> GetPresignedUploadUrlAsync(string objectName, int expirationSeconds = 3600)
    {
        try
        {
            var url = await _minioClient.PresignedPutObjectAsync(
                new PresignedPutObjectArgs()
                    .WithBucket(_bucketName)
                    .WithObject(objectName)
                    .WithExpiry(expirationSeconds));

            _logger.LogInformation("Generated presigned upload URL for object: {ObjectName}", objectName);
            return url;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating presigned upload URL for object: {ObjectName}", objectName);
            throw;
        }
    }

    public async Task DeleteFileAsync(string objectName)
    {
        try
        {
            await _minioClient.RemoveObjectAsync(
                new RemoveObjectArgs()
                    .WithBucket(_bucketName)
                    .WithObject(objectName));

            _logger.LogInformation("File deleted successfully: {ObjectName}", objectName);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting file: {ObjectName}", objectName);
            throw;
        }
    }
}

