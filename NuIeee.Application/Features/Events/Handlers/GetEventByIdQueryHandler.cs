using MediatR;
using NuIeee.Application.DTOs.Events;
using NuIeee.Application.Features.Events.Queries;
using NuIeee.Application.Interfaces;

namespace NuIeee.Application.Features.Events.Handlers;

public class GetEventByIdQueryHandler(IEventRepository eventRepository) : IRequestHandler<GetEventByIdQuery, EventDto>
{
    public async Task<EventDto> Handle(GetEventByIdQuery request, CancellationToken cancellationToken)
    {
        var eventEntity = await eventRepository.GetEventAsync(request.id, cancellationToken);
        var eventDto = new EventDto
        {
            Id = eventEntity.Id,
            Title = eventEntity.Title,
            Description = eventEntity.Description,
            EventDateTime = eventEntity.EventDateTime,
            HasRegistrationLink = eventEntity.HasRegistrationLink,
            RegistrationLink = eventEntity.RegistrationLink,
            Photos = eventEntity.EventPhotos.Select(photo => new EventPhotoDto
            {
                Id = photo.Id,
                PhotoLink = photo.PhotoLink,
                AlternativeText = photo.AlternativeText,
            }).ToList()
        };
        
        return eventDto;
    }
}