using System.ComponentModel.DataAnnotations.Schema;

namespace NuIeee.Domain.Entities;

[Table("Teams")]
public class Team : BaseEntity
{
    public string Name { get; set; }
    
    public List<TeamMember> Members { get; set; }
}