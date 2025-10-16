namespace NuIeee.Application.DTOs.Events;

public class EventDto
{
    public Guid Id { get; set; }
    public string Title { get; set; }
    public string Description { get; set; }
    public DateTime EventDateTime { get; set; }
    public bool HasRegistrationLink { get; set; }
    public Uri? RegistrationLink { get; set; }

    public List<EventPhotoDto> Photos { get; set; }
}