using NuIeee.Application.DTOs.Hackathon;
using NuIeee.Application.Interfaces;
using NuIeee.Domain.Entities;

namespace NuIeee.Application.Services.Hackathon;

public class HackathonService : IHackathonService
{
    private readonly IHackathonRepository _hackathonRepository;

    public HackathonService(IHackathonRepository hackathonRepository)
    {
        _hackathonRepository = hackathonRepository;
    }

    public async Task<List<HackathonTeamDto>> GetHackathonTeamsAsync(CancellationToken cancellationToken = default)
    {
        return await _hackathonRepository.GetHackathonTeamsAsync(cancellationToken);
    }

    public async Task RegisterTeamAsync(RegisterTeamDto registerTeamDto, CancellationToken cancellationToken = default)
    {
        var team = new Team
        {
            Name = registerTeamDto.TeamName,
            Members = registerTeamDto.Members.Select((dto, index) => new TeamMember
            {
                FullName = dto.FullName,
                NuId = dto.NuId,
                Iin = dto.Iin,
                Email = dto.Email,
                YearOfStudy = dto.YearOfStudy,
                Major = dto.Major,
                IsCaptain = index == 0 // First member is the captain
            }).ToList()
        };

        await _hackathonRepository.AddTeamAsync(team, cancellationToken);
    }
}
