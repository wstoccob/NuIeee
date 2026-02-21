namespace NuIeee.Application.DTOs.Events;

public class CreateEventDto
{
    public string Title { get; set; }
    public string Description { get; set; }
    public DateTime EventDateTime { get; set; }
    public Uri? RegistrationLink { get; set; }
    public List<EventPhotoDto> Photos { get; set; }
}
