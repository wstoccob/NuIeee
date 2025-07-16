using MediatR;
using NuIeee.Application.DTOs.Hackathon;

namespace NuIeee.Application.Features.Hackathon.Commands;

public record RegisterTeamCommand(string TeamName, List<TeamMemberDto> Members) : IRequest;