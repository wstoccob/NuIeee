using NuIeee.Application.DTOs.Events;

namespace NuIeee.Application.Services.Events;

public interface IEventService
{
    Task<List<EventDto>> GetAllEventsAsync(CancellationToken cancellationToken = default);
    Task<EventDto> GetEventByIdAsync(Guid id, CancellationToken cancellationToken = default);
    Task<List<EventDto>> GetLastCountEventsAsync(int count, CancellationToken cancellationToken = default);
    Task<Guid> CreateEventAsync(CreateEventDto createEventDto, CancellationToken cancellationToken = default);
    Task<bool> UpdateEventAsync(EventDto eventDto, CancellationToken cancellationToken = default);
    Task<bool> DeleteEventAsync(Guid id, CancellationToken cancellationToken = default);
}
