using MediatR;
using NuIeee.Application.DTOs.Events;
using NuIeee.Application.Features.Events.Queries;
using NuIeee.Application.Interfaces;

namespace NuIeee.Application.Features.Events.Handlers;

public class GetLastCountEventsQueryHandler(IEventRepository eventRepository) : IRequestHandler<GetLastCountEventsQuery, List<EventDto>>
{
    public async Task<List<EventDto>> Handle(GetLastCountEventsQuery request, CancellationToken cancellationToken)
    {
        var eventEntities = await eventRepository.GetLastCountEventsAsync(request.Count, cancellationToken);
        
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