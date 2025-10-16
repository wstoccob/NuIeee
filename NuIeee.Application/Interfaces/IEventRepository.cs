using EventEntity = NuIeee.Domain.Entities.Event;

namespace NuIeee.Application.Interfaces;

public interface IEventRepository
{
    Task<Guid> AddEventAsync(EventEntity eventEntity, CancellationToken cancellationToken);
}