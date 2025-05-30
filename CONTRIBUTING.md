## Contributing Guidelines

Thank you for considering contributing to this Python project! To ensure a smooth workflow and maintain high code quality, please follow these guidelines.

## 📌 General Guidelines

- Ensure your code follows the [Python Development Conventions](./CODE_CONVENTION.md) for code structure, naming conventions, and best practices.
- All new features and bug fixes should be tested before submitting a pull request.
- Write meaningful commit messages and follow the branching rules outlined below.
- Avoid introducing unnecessary dependencies or large libraries without discussion.
- Keep PRs small and focused on a single feature or fix.

## 📂 Project Structure

Make sure to follow the defined structure when adding new files or modifying existing ones:

- `helper/` → Utility functions
- `validator/` → Function for validating input and output
- `models/` → Initialized models in class
- `requirements.txt` → Project dependencies
- `.config/` → Configuration folder for scraping config
- `app.py` → main code for setting Flask endpoint

## 🌱 Branching Strategy

We follow the **Git Flow** branching strategy:

- **`main`**: Always contains stable, production-ready code.
- **`dev_staging`**: The staging-ready branch for testing before deployment.
- **`feature`**: The active development branch where all features and fixes are merged.
- **Feature branches** (`dev/your-name/feature-name`: Used for fixing bugs in `feature`.

  **Note: You need to create branches following example below**
- **Release branches** (`release/version`: Used for final testing before deploying to `main`.

**Example Workflow:**

1. Create a new branch from `feature`: `git checkout -b feature/new-endpoint`
2. Work on your feature, and commit regularly.
3. Push your branch: `git push origin feature/new-endpoint` to `feature`
4. Open a pull request (PR) to `feature`.
5. Wait for review, make necessary changes, and merge.

## 🔥 Commit Message Guidelines

Follow the conventional commit format:

```
<type>(<scope>): <message>
```

**Examples:**

- `feat(auth): add JWT authentication`
- `fix(api): resolve user profile retrieval bug`
- `docs(readme): update installation instructions`
- `chore(deps): update Flask dependencies`

## 🔍 Code Review Process

1. Submit a PR following the PR template.

   PR Template :

     1/ title : <dev_source> to <dev_target> DD/MM/YYYY hh:mm (Timezone)
        ---> Example : dev/zain/lebon_stage to feature/lebon_stage 19/02/2025 10:00 (GMT +7)
   
     2/ Comment :
        ---> Have a list of changes
        ---> Have attachment video/screenshot
        ---> Have a summary explaining what was done for the PR
     
     3/ Reviewer: "Ade"
   
2. At least one team member must review and approve before merging.
3. Fix any requested changes promptly.
4. PRs should not be merged directly into `main`.

  **NOTE: Ensure there is no conflict from your branch to your target branch**

## ❓ Need Help?
If you have any questions or need further clarification, reach out or open an issue.

Happy coding and strive to make it happen! 🚀