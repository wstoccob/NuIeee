using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using NuIeee.Application.DTOs.Events;
using NuIeee.Application.Services.Events;

namespace NuIeee.WebApi.Controllers;

[ApiController]
[Route("api/events")]
public class EventsController(IEventService eventService) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> GetAllEvents(CancellationToken cancellationToken)
    {
        var result = await eventService.GetAllEventsAsync(cancellationToken);
        return Ok(result);
    }
    
    [HttpGet("{id:guid}")]
    public async Task<IActionResult> GetEventByIdAsync(Guid id, CancellationToken cancellationToken)
    {
        var result = await eventService.GetEventByIdAsync(id, cancellationToken);
        return Ok(result);
    }

    [HttpGet("last/{count:int}")]
    public async Task<IActionResult> GetLastCountEventsAsync(int count, CancellationToken cancellationToken)
    {
        var result = await eventService.GetLastCountEventsAsync(count, cancellationToken);
        return Ok(result);
    }
    
    [Authorize(Roles="Admin, SuperAdmin")]
    [HttpPost("create-event")]
    public async Task<IActionResult> CreateEventAsync([FromBody] CreateEventDto createEventDto)
    {
        var id = await eventService.CreateEventAsync(createEventDto);
        return Ok(id);
    }
    
    [Authorize(Roles="Admin, SuperAdmin")]
    [HttpPut("update-event")]
    public async Task<IActionResult> UpdateEventAsync([FromBody] EventDto eventDto, CancellationToken cancellationToken)
    {
        var result = await eventService.UpdateEventAsync(eventDto, cancellationToken);
        if (!result)
        {
            return BadRequest("Failed to update the event.");
        }
        
        return Ok(result);
    }

    [Authorize(Roles = "Admin, SuperAdmin")]
    [HttpDelete("delete-event/{id:guid}")]
    public async Task<IActionResult> DeleteEventAsync(Guid id, CancellationToken cancellationToken)
    {
        var result = await eventService.DeleteEventAsync(id, cancellationToken);
        if (!result)
        {
            return BadRequest("Failed to delete the event.");
        }
        
        return Ok(result);
    }
}
