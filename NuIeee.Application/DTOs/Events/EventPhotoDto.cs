namespace NuIeee.Application.DTOs.Events;

public class EventPhotoDto
{
    public Guid Id { get; set; }
    public string AlternativeText { get; set; }
    public Uri PhotoLink { get; set; }
}