using NuIeee.Application.DTOs.Hackathon;

namespace NuIeee.Application.Services.Hackathon;

public interface IHackathonService
{
    Task<List<HackathonTeamDto>> GetHackathonTeamsAsync(CancellationToken cancellationToken = default);
    Task RegisterTeamAsync(RegisterTeamDto registerTeamDto, CancellationToken cancellationToken = default);
}
