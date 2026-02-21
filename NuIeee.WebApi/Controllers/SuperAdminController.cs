using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using NuIeee.Application.DTOs.Identity;
using NuIeee.Application.Services.Users;

namespace NuIeee.WebApi.Controllers;

[ApiController]
[Route("api/superadmin")]
[Authorize(Roles = "SuperAdmin")]
public class SuperAdminController(IUserService userService) : ControllerBase
{
    [HttpGet("users")]
    public async Task<IActionResult> GetAllUsersAsync()
    {
        try
        {
            var result = await userService.GetAllUsersAsync();
            return Ok(new { result });
        }
        catch (Exception ex)
        {
            return StatusCode(500, ex.Message);
        }
    }

    [HttpGet("users/{userId}")]
    public async Task<IActionResult> GetUserByIdAsync(Guid userId)
    {
        try
        {
            var result = await userService.GetUserByIdAsync(userId);
            return Ok(new { result });
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, ex.Message);
        }
    }

    [HttpPost("create-user")]
    public async Task<IActionResult> CreateUserAsync([FromBody] CreateUserDto createUserDto)
    {
        try
        {
            var result = await userService.CreateUserAsync(
                createUserDto.Username, 
                createUserDto.Fullname, 
                createUserDto.Password, 
                createUserDto.Role);
            return Ok(new { result });
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, ex.Message);
        }
    }

    [HttpDelete("delete-user")]
    public async Task<IActionResult> DeleteUserAsync([FromBody] DeleteUserDto deleteUserDto)
    {
        try
        {
            await userService.DeleteUserAsync(deleteUserDto.UserId);
            return Ok();
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            return StatusCode(500, ex.Message);
        }
    }
}
