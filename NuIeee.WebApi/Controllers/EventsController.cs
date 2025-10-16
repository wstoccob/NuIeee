using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using NuIeee.Application.Features.Events.Commands;

namespace NuIeee.WebApi.Controllers;

[ApiController]
[Route("api/events")]
public class EventsController(IMediator mediator) : ControllerBase
{
    /*[HttpGet]
    public async Task<IActionResult> GetAllEvents()
    {
        var result = await mediator.Send();
        return Ok(result);
    }*/
    
    [Authorize(Roles="SuperAdmin")]
    [HttpPost("create-event")]
    public async Task<IActionResult> CreateEventAsync(CreateEventCommand command)
    {
        var id = await mediator.Send(command);
        return Ok(id);
    }
}