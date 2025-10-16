using System.ComponentModel.DataAnnotations.Schema;

namespace NuIeee.Domain.Entities;

[Table("EventPhotos")]
public class EventPhoto : BaseEntity
{
    public string AlternativeText { get; set; }
    public Uri PhotoLink { get; set; }
    
    // Foreign key
    public Guid EventId { get; set; }
    public Event Event { get; set; }
}