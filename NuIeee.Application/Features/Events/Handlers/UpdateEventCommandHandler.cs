using MediatR;
using NuIeee.Application.Features.Events.Commands;
using NuIeee.Application.Interfaces;
using NuIeee.Domain.Entities;
using EventEntity = NuIeee.Domain.Entities.Event;

namespace NuIeee.Application.Features.Events.Handlers;

public class UpdateEventCommandHandler(IEventRepository eventRepository): IRequestHandler<UpdateEventCommand, bool>
{
    public async Task<bool> Handle(UpdateEventCommand request, CancellationToken cancellationToken)
    {
        var eventEntity = new EventEntity
        {
            Id = request.eventDto.Id,
            Title = request.eventDto.Title,
            Description = request.eventDto.Description,
            EventDateTime = request.eventDto.EventDateTime,
            HasRegistrationLink = request.eventDto.HasRegistrationLink,
            RegistrationLink = request.eventDto.RegistrationLink,
            EventPhotos = request.eventDto.Photos.Select(photo => new EventPhoto
            {
                Id = photo.Id,
                PhotoLink = photo.PhotoLink,
                AlternativeText = photo.AlternativeText,
            }).ToList()
        };
        
        var result = await eventRepository.UpdateEventAsync(eventEntity, cancellationToken);
        
        return result;
    }
}