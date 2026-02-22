using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using NuIeee.Application.Services.MinIO;

namespace NuIeee.WebApi.Controllers;

[ApiController]
[Route("api/minio")]
[Authorize(Roles="Admin, SuperAdmin")]
public class MinioController : ControllerBase
{
    private readonly IMinioService _minioService;
    private readonly ILogger<MinioController> _logger;

    public MinioController(IMinioService minioService, ILogger<MinioController> logger)
    {
        _minioService = minioService;
        _logger = logger;
    }

    [HttpPost("upload-url")]
    public async Task<IActionResult> GetUploadUrl([FromQuery] string fileName, [FromQuery] int expirationSeconds = 3600)
    {
        try
        {
            var url = await _minioService.GetPresignedUploadUrlAsync(fileName, expirationSeconds);
            return Ok(new { uploadUrl = url, fileName = fileName });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting upload URL");
            return StatusCode(500, new { error = "Failed to generate upload URL" });
        }
    }

    [HttpDelete("delete/{fileName}")]
    public async Task<IActionResult> DeleteFile(string fileName)
    {
        try
        {
            await _minioService.DeleteFileAsync(fileName);
            return Ok(new { message = "File deleted successfully" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting file");
            return StatusCode(500, new { error = "Failed to delete file" });
        }
    }
}

