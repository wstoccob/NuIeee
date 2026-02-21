using NuIeee.Application.DTOs.Events;
using NuIeee.Application.Interfaces;
using NuIeee.Domain.Entities;
using EventEntity = NuIeee.Domain.Entities.Event;

namespace NuIeee.Application.Services.Events;

public class EventService : IEventService
{
    private readonly IEventRepository _eventRepository;

    public EventService(IEventRepository eventRepository)
    {
        _eventRepository = eventRepository;
    }

    public async Task<List<EventDto>> GetAllEventsAsync(CancellationToken cancellationToken = default)
    {
        var eventEntities = await _eventRepository.GetAllEventsAsync(cancellationToken);
        return MapToEventDtos(eventEntities);
    }

    public async Task<EventDto> GetEventByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        var eventEntity = await _eventRepository.GetEventAsync(id, cancellationToken);
        return MapToEventDto(eventEntity);
    }

    public async Task<List<EventDto>> GetLastCountEventsAsync(int count, CancellationToken cancellationToken = default)
    {
        var eventEntities = await _eventRepository.GetLastCountEventsAsync(count, cancellationToken);
        return MapToEventDtos(eventEntities);
    }

    public async Task<Guid> CreateEventAsync(CreateEventDto createEventDto, CancellationToken cancellationToken = default)
    {
        var eventEntity = new EventEntity
        {
            Title = createEventDto.Title,
            Description = createEventDto.Description,
            EventDateTime = createEventDto.EventDateTime,
            HasRegistrationLink = createEventDto.RegistrationLink is not null,
            RegistrationLink = createEventDto.RegistrationLink,
            CreatedAt = DateTime.Now,
            EventPhotos = createEventDto.Photos.Select(e => new EventPhoto
            {
                AlternativeText = e.AlternativeText,
                PhotoLink = e.PhotoLink,
            }).ToList(),
        };

        var id = await _eventRepository.AddEventAsync(eventEntity, cancellationToken);
        return id;
    }

    public async Task<bool> UpdateEventAsync(EventDto eventDto, CancellationToken cancellationToken = default)
    {
        var eventEntity = new EventEntity
        {
            Id = eventDto.Id,
            Title = eventDto.Title,
            Description = eventDto.Description,
            EventDateTime = eventDto.EventDateTime,
            HasRegistrationLink = eventDto.HasRegistrationLink,
            RegistrationLink = eventDto.RegistrationLink,
            EventPhotos = eventDto.Photos.Select(photo => new EventPhoto
            {
                Id = photo.Id,
                PhotoLink = photo.PhotoLink,
                AlternativeText = photo.AlternativeText,
            }).ToList()
        };

        var result = await _eventRepository.UpdateEventAsync(eventEntity, cancellationToken);
        return result;
    }

    public async Task<bool> DeleteEventAsync(Guid id, CancellationToken cancellationToken = default)
    {
        var result = await _eventRepository.DeleteEventAsync(id, cancellationToken);
        return result;
    }

    private EventDto MapToEventDto(EventEntity eventEntity)
    {
        return new EventDto
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
    }

    private List<EventDto> MapToEventDtos(List<EventEntity> eventEntities)
    {
        return eventEntities.Select(MapToEventDto).ToList();
    }
}
