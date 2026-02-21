using Microsoft.AspNetCore.Mvc;
using NuIeee.Application.DTOs.Auth;
using NuIeee.Application.Services.Auth;

namespace NuIeee.WebApi.Controllers;

[ApiController]
[Route("api/auth")]
public class AuthController(IAuthService authService) : ControllerBase
{
    [HttpPost("login")]
    public async Task<IActionResult> LoginAsync([FromBody] LoginDto dto)
    {
        try
        {
            var token = await authService.LoginAsync(dto);
            return Ok(new { token });
        }
        catch (Exception ex)
        {
            return Unauthorized(ex.Message);
        }
    }

    [HttpPost("register")]
    public async Task<IActionResult> RegisterAsync([FromBody] RegisterDto registerDto)
    {
        try
        {
            var userId = await authService.RegisterAsync(registerDto.Username, registerDto.Password);
            return Ok(new { userId });
        }
        catch (Exception ex)
        {
            return StatusCode(500, ex.Message);
        }
    }
}
