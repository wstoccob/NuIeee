using NuIeee.Domain.Entities;

namespace NuIeee.Application.Interfaces;

public interface IHackathonRepository
{
    Task AddTeamAsync(Team team, CancellationToken cancellationToken);
}