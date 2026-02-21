using NuIeee.Application.DTOs.Hackathon;

namespace NuIeee.Application.Services.Hackathon;

public class RegisterTeamDto
{
    public string TeamName { get; set; }
    public List<TeamMemberDto> Members { get; set; }
}
