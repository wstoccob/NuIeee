namespace NuIeee.Application.DTOs.Events;

public class EventDto
{
    public string Title { get; set; }
    public string Description { get; set; }
    public DateTime EventDateTime { get; set; }
    public bool HasRegistrationLink { get; set; }
    public Uri? RegistrationLink { get; set; }

    private List<EventPhotoDto> Photos { get; set; }
}