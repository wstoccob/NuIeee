using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using NuIeee.Application.Features.Events.Commands;
using NuIeee.Application.Features.Events.Queries;

namespace NuIeee.WebApi.Controllers;

[ApiController]
[Route("api/events")]
public class EventsController(IMediator mediator) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> GetAllEvents(CancellationToken cancellationToken)
    {
        var result = await mediator.Send(new GetAllEventsQuery(), cancellationToken);
        return Ok(result);
    }
    
    [HttpGet("/{id:guid}")]
    public async Task<IActionResult> GetEventByIdAsync(Guid id, CancellationToken cancellationToken)
    {
        var result = await mediator.Send(new GetEventByIdQuery(id), cancellationToken);
        
        return Ok(result);
    }
    
    [Authorize(Roles="SuperAdmin")]
    [HttpPost("create-event")]
    public async Task<IActionResult> CreateEventAsync(CreateEventCommand command)
    {
        var id = await mediator.Send(command);
        return Ok(id);
    }
}