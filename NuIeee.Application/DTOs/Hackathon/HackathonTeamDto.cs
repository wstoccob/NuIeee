namespace NuIeee.Application.DTOs.Hackathon;

public class HackathonTeamDto
{
    public string TeamName { get; set; } = string.Empty;
    public List<TeamMemberDto> Members { get; set; } = [];
}