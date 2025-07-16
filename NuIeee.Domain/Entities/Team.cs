namespace NuIeee.Domain.Entities;

public class Team : BaseEntity
{
    public string Name { get; set; }
    
    public List<TeamMember> Members { get; set; }
}