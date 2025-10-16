using MediatR;
using NuIeee.Application.Features.Events.Commands;
using NuIeee.Application.Interfaces;
using NuIeee.Domain.Entities;
using EventEntity = NuIeee.Domain.Entities.Event;

namespace NuIeee.Application.Features.Events.Handlers;

public class CreateEventCommandHandler(IEventRepository eventRepository) : IRequestHandler<CreateEventCommand, Guid>
{
    public async Task<Guid> Handle(CreateEventCommand request, CancellationToken cancellationToken)
    {
        var eventEntity = new EventEntity
        {
            Title = request.Title,
            Description = request.Description,
            EventDateTime = request.EventDateTime,
            HasRegistrationLink = request.RegistrationLink is not null,
            RegistrationLink = request.RegistrationLink,
            CreatedAt = DateTime.Now,
            EventPhotos = request.Photos.Select(e => new EventPhoto
            {
                AlternativeText = e.AlternativeText,
                PhotoLink = e.PhotoLink,
            }).ToList(),
        };
        
        var id = await eventRepository.AddEventAsync(eventEntity, cancellationToken);
        return id;
    }
}