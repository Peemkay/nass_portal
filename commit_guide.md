# Guide to Committing Changes to GitHub

## Step 1: Make Changes to Your Files
Edit the files in your project as needed. You can add, modify, or delete files.

## Step 2: Check the Status of Your Repository
Open your terminal and navigate to your project directory. Use the following command to see the status of your repository and which files have been changed:

```bash
git status
```

## Step 3: Stage Your Changes
To prepare your changes for commit, you need to stage them. You can stage specific files or all changes. 

- To stage specific files, use:
  ```bash
  git add <file1> <file2>
  ```
  For example:
  ```bash
  git add app.py static/css/style.css
  ```

- To stage all changes, use:
  ```bash
  git add .
  ```

## Step 4: Commit Your Changes
Once your changes are staged, you can commit them with a message describing what you changed. Use the following command:

```bash
git commit -m "Your commit message here"
```

For example:
```bash
git commit -m "Updated app.py to fix bug in user login"
```

## Step 5: Push Your Changes to GitHub
After committing your changes, you can push them to your remote repository on GitHub:

```bash
git push origin main
```

## Summary of Commands
1. Check status: `git status`
2. Stage changes: `git add .` (or `git add <specific files>`)
3. Commit changes: `git commit -m "Your commit message"`
4. Push changes: `git push origin main`
