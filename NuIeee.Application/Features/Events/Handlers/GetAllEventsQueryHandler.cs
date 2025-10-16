using MediatR;
using NuIeee.Application.DTOs.Events;
using NuIeee.Application.Features.Events.Queries;
using NuIeee.Application.Interfaces;

namespace NuIeee.Application.Features.Events.Handlers;

public class GetAllEventsQueryHandler(IEventRepository eventRepository) : IRequestHandler<GetAllEventsQuery, List<EventDto>>
{
    public async Task<List<EventDto>> Handle(GetAllEventsQuery request, CancellationToken cancellationToken)
    {
        var eventEntities = await eventRepository.GetAllEventsAsync(cancellationToken);
        var eventDtos = eventEntities.Select(e => new EventDto
        {
            Id = e.Id,
            Title = e.Title,
            Description = e.Description,
            EventDateTime = e.EventDateTime,
            HasRegistrationLink = e.HasRegistrationLink,
            RegistrationLink = e.RegistrationLink,
            Photos = e.EventPhotos.Select(ep => new EventPhotoDto
            {
                Id = ep.Id,
                PhotoLink = ep.PhotoLink,
                AlternativeText = ep.AlternativeText,
            }).ToList()
        }).ToList();

        return eventDtos;
    }
}