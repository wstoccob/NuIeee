using System.ComponentModel.DataAnnotations.Schema;

namespace NuIeee.Domain.Entities;

[Table("Events")]
public class Event : BaseEntity
{
    public string Title { get; set; }
    public string Description { get; set; }
    public DateTime EventDateTime { get; set; }
    public bool HasRegistrationLink { get; set; }
    public Uri? RegistrationLink { get; set; }

    public List<EventPhoto> EventPhotos { get; set; }
}