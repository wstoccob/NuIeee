using MediatR;
using Microsoft.AspNetCore.Mvc;
using NuIeee.Application.Features.Hackathon;
using NuIeee.Application.Features.Hackathon.Commands;

namespace NuIeee.WebApi.Controllers;

[ApiController]
[Route("api/hackathon")]
public class HackathonController(IMediator _mediator) : ControllerBase
{
    [HttpGet("get-hackathon-teams")]
    public async Task<IActionResult> GetHackathonTeamsAsync()
    {
        var result = await _mediator.Send(new GetHackathonTeamsQuery());
        return Ok(result);
    }
    
    [HttpPost("register-team")]
    public async Task<IActionResult> RegisterTeamAsync(RegisterTeamCommand command)
    {
        await _mediator.Send(command);
        
        return Ok();
    }
}