# NU IEEE Website

This is the official backend for the **Nazarbayev University IEEE Student Branch** website, built using **ASP.NET Core Web API**, **PostgreSQL**, and **Clean Architecture + CQRS**.

Frontend is written in **React + TypeScript + TailwindCSS** (hosted separately).

---

## 🔧 Tech Stack

- **ASP.NET Core 8**
- **PostgreSQL**
- **Entity Framework Core**
- **MediatR** (CQRS pattern)
- **JWT Authentication**
- **Clean Architecture**

---

## 📂 Project Structure
NuIeee/
 - ├── NuIeee.Domain/ → Core domain models, enums, etc.
 - ├── NuIeee.Application/ → DTOs, CQRS handlers, interfaces
 - ├── NuIeee.Infrastructure/ → EF Core, Identity, JWT logic
 - ├── NuIeee.WebApi/ → Entry point, controllers, DI setup

---

## 🚀 Getting Started

## 🛠 Prerequisites

- [.NET 8 SDK](https://dotnet.microsoft.com/en-us/download/dotnet/8.0)
- [PostgreSQL](https://www.postgresql.org/download/)
- [EF Core CLI tools](https://learn.microsoft.com/en-us/ef/core/cli/dotnet)

## 🔑 Secrets Setup

We use `UserSecrets` to store sensitive values like the JWT key.

Run this to initialize secrets:

```bash
dotnet user-secrets init --project NuIeee.WebApi
dotnet user-secrets set "Jwt:Key" "your_super_secret__jwt_key" --project NuIeee.WebApi
dotnet user-secrets set "DefaultConnection" "your_super_secret_database_key" --project NuIeee.WebApi
```
Super secret keys can be obtained in Telegram Group. Do not share them with others and do not push them to repository! 😡

## 🚀 Run the project

To run, you need .NET Runtime and .NET SDK 8.0

```bash
dotnet run --project .\NuIeee.WebApi\
```

## 🔧 Collaborate

To collaborate, create your own branch, make changes and start a Merge Request.

Good luck!

