namespace NuIeee.Domain.Entities;

public class TeamMember : BaseEntity
{
    public string FullName { get; set; }
    public string? NuId { get; set; }
    public string? Iin { get; set; }
    public string Email { get; set; }
    public string YearOfStudy { get; set; }
    public string Major { get; set; }

    // Foreign key
    public Guid TeamId { get; set; }
    public Team Team { get; set; }
}