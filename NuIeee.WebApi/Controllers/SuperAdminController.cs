using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using NuIeee.Application.Features.Users.Commands;
using NuIeee.Application.Features.Users.Queries;
using NuIeee.Domain.Entities;
using NuIeee.Infrastructure.Identity;

namespace NuIeee.WebApi.Controllers;

[ApiController]
[Route("api/superadmin")]
[Authorize(Roles = "SuperAdmin")]
public class SuperAdminController : ControllerBase
{
    private readonly IMediator _mediator;

    public SuperAdminController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpGet("users")]
    public async Task<IActionResult> GetAllUsersAsync()
    {
        try
        {
            var result = await _mediator.Send(new GetAllUsersQuery());
            return Ok(result);
        }
        catch (Exception ex)
        {
            return StatusCode(500, ex);
        }
    }

    [HttpGet("users/{userId}")]
    public async Task<IActionResult> GetUserByIdAsync(Guid userId)
    {
        try
        {
            var result = await _mediator.Send(new GetUserByIdQuery(userId));
            return Ok(result);
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
    public async Task<IActionResult> CreateUserAsync(CreateUserCommand command)
    {
        try
        {
            var result = await _mediator.Send(command);
            return Ok(result);
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
    public async Task<IActionResult> DeleteUserAsync(DeleteUserCommand command)
    {
        try
        {
            await _mediator.Send(command);
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
