using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using NuIeee.Application.Services.Hackathon;

namespace NuIeee.WebApi.Controllers;

[ApiController]
[Route("api/hackathon")]
public class HackathonController(IHackathonService hackathonService) : ControllerBase
{
    [Authorize(Roles="SuperAdmin")]
    [HttpGet("get-hackathon-teams")]
    public async Task<IActionResult> GetHackathonTeamsAsync()
    {
        var result = await hackathonService.GetHackathonTeamsAsync();
        return Ok(result);
    }
    
    [HttpPost("register-team")]
    public async Task<IActionResult> RegisterTeamAsync([FromBody] RegisterTeamDto registerTeamDto)
    {
        await hackathonService.RegisterTeamAsync(registerTeamDto);
        return Ok();
    }
}
