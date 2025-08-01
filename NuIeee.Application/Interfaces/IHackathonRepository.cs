using NuIeee.Application.DTOs.Hackathon;
using NuIeee.Domain.Entities;

namespace NuIeee.Application.Interfaces;

public interface IHackathonRepository
{
    Task AddTeamAsync(Team team, CancellationToken cancellationToken);
    
    Task<List<HackathonTeamDto>> GetHackathonTeamsAsync(CancellationToken cancellationToken);
}