﻿using MediatR;
using Microsoft.AspNetCore.Mvc;
using NuIeee.Application.DTOs.Auth;
using NuIeee.Application.Features.Auth.Commands;
using NuIeee.Application.Features.Auth.Queries;

namespace NuIeee.WebApi.Controllers;


[ApiController]
[Route("api/auth")]
public class AuthController : ControllerBase
{
    private readonly IMediator _mediator;

    public AuthController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpPost("login")]
    public async Task<IActionResult> LoginAsync([FromBody] LoginDto dto)
    {
        try
        {
            var token = await _mediator.Send(new LoginQuery(dto));

            return Ok(new { token });
        }
        catch (Exception ex)
        {
            return Unauthorized(ex.Message);
        }
    }

    [HttpPost("register")]
    public async Task<IActionResult> RegisterAsync([FromBody] RegisterCommand registerCommand)
    {
        try
        {
            var userId = await _mediator.Send(registerCommand);
            return Ok(new { userId });
        }
        catch(Exception ex)
        {
            return StatusCode(500, ex.Message);
        }
    }
}
