using EventEntity = NuIeee.Domain.Entities.Event;

namespace NuIeee.Application.Interfaces;

public interface IEventRepository
{
    Task<Guid> AddEventAsync(EventEntity eventEntity, CancellationToken cancellationToken);
    
    Task<List<EventEntity>> GetAllEventsAsync(CancellationToken cancellationToken);
    
    Task<EventEntity> GetEventAsync(Guid id, CancellationToken cancellationToken);
    
    Task<List<EventEntity>> GetLastCountEventsAsync(int count, CancellationToken cancellationToken);
}