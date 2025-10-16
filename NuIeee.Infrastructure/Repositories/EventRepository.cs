using NuIeee.Application.Interfaces;
using NuIeee.Domain.Entities;
using NuIeee.Infrastructure.Persistence;
using EventEntity = NuIeee.Domain.Entities.Event;

namespace NuIeee.Infrastructure.Repositories;

public class EventRepository(ApplicationDbContext _context) : IEventRepository
{
    public async Task<Guid> AddEventAsync(EventEntity eventEntity, CancellationToken cancellationToken)
    {
        await _context.Events.AddAsync(eventEntity, cancellationToken);
        await _context.SaveChangesAsync(cancellationToken);
        
        return eventEntity.Id;
    }
}