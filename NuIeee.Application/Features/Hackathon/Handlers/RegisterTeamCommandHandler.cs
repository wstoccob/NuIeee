using MediatR;
using NuIeee.Application.Features.Hackathon.Commands;
using NuIeee.Application.Interfaces;
using NuIeee.Domain.Entities;

namespace NuIeee.Application.Features.Hackathon.Handlers;

public class RegisterTeamCommandHandler : IRequestHandler<RegisterTeamCommand>
{
    private readonly IHackathonRepository _hackathonRepository;

    public RegisterTeamCommandHandler(IHackathonRepository  hackathonRepository)
    {
        _hackathonRepository = hackathonRepository;
    }
    public async Task Handle(RegisterTeamCommand request, CancellationToken cancellationToken)
    {
        var team = new Team
        {
            Name = request.TeamName,
            Members = request.Members.Select((dto, index) => new TeamMember
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