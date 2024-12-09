# Photo Organizer

A user-friendly Python desktop application that helps you organize your photos using image metadata automatically. The application provides basic graphical interface for managing and organizing your photo collection.

## Features

- **Automatic Date Organization**: Organizes photos into folders based on their creation date
- **EXIF Data Support**: Extracts original photo date from EXIF metadata when available
- **Flexible Operation Modes**: Choose between copying or moving photos
- **Custom Folder Creation**: Create new destination folders directly from the application
- **Progress Tracking**: Real-time progress bar and status updates during organization
- **Error Handling**: Robust error handling with user-friendly error messages
- **Modern UI**: Clean and intuitive interface with hover effects and scrolling support

## Installation

### Run the Executable (Windows)
1. Navigate to the `dist` folder
2. Double-click `PhotoOrganizer.exe`
3. No additional installation or Python required

## Usage

1. Launch the application
2. Select source folder containing your photos
3. Choose or create a destination folder
4. Select operation mode (Copy/Move)
5. Click "Organize Photos" to start the process
6. Use the "View Organized Photos" button to see the results

## Folder Structure

Photos will be organized in the following structure:
```
destination_folder/
├── 2024/
│   ├── January/
│   ├── February/
│   └── ...
├── 2023/
│   ├── December/
│   └── ...
└── ...
```

