using Microsoft.EntityFrameworkCore;
using NuIeee.Application.Interfaces;
using NuIeee.Domain.Entities;
using NuIeee.Infrastructure.Persistence;
using EventEntity = NuIeee.Domain.Entities.Event;

namespace NuIeee.Infrastructure.Repositories;

public class EventRepository(ApplicationDbContext dbContext) : IEventRepository
{
    public async Task<Guid> AddEventAsync(EventEntity eventEntity, CancellationToken cancellationToken)
    {
        await dbContext.Events.AddAsync(eventEntity, cancellationToken);
        await dbContext.SaveChangesAsync(cancellationToken);
        
        return eventEntity.Id;
    }

    public async Task<List<EventEntity>> GetAllEventsAsync(CancellationToken cancellationToken)
    {
        var events = await dbContext.Events
            .Include(e => e.EventPhotos)
            .OrderByDescending(e => e.EventDateTime)
            .ToListAsync(cancellationToken);
        
        return events;
    }

    public async Task<Event> GetEventAsync(Guid id, CancellationToken cancellationToken)
    {
        var eventEntity = await dbContext.Events
            .Include(e => e.EventPhotos)
            .FirstOrDefaultAsync(e => e.Id == id, cancellationToken);
        
        return eventEntity;
    }
}