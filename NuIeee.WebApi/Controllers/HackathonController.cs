using MediatR;
using Microsoft.AspNetCore.Mvc;
using NuIeee.Application.Features.Hackathon.Commands;

namespace NuIeee.WebApi.Controllers;

[ApiController]
[Route("api/hackathon")]
public class HackathonController(IMediator _mediator) : ControllerBase
{
    [HttpPost("register-team")]
    public async Task<IActionResult> RegisterTeamAsync(RegisterTeamCommand command)
    {
        await _mediator.Send(command);
        
        return Ok();
    }
}