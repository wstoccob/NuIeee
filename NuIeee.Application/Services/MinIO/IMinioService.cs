namespace NuIeee.Application.Services.MinIO;

public interface IMinioService
{
    Task<string> GetPresignedUploadUrlAsync(string objectName, int expirationSeconds = 3600);

    Task DeleteFileAsync(string objectName);
}