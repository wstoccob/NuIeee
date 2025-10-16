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

    [HttpGet("/last/{count:int}")]
    public async Task<IActionResult> GetLastCountEventsAsync(int count, CancellationToken cancellationToken)
    {
        var result = await mediator.Send(new GetLastCountEventsQuery(count), cancellationToken);
        
        return Ok(result);
    }
    
    [Authorize(Roles="Admin, SuperAdmin")]
    [HttpPost("create-event")]
    public async Task<IActionResult> CreateEventAsync(CreateEventCommand command)
    {
        var id = await mediator.Send(command);
        return Ok(id);
    }
    
    [Authorize(Roles="Admin, SuperAdmin")]
    [HttpPut("update-event")]
    public async Task<IActionResult> UpdateEventAsync(UpdateEventCommand command, CancellationToken cancellationToken)
    {
        var result = await mediator.Send(command, cancellationToken);
        if (!result)
        {
            return BadRequest("Failed to update the event.");
        }
        
        return Ok(result);
    }
    
}