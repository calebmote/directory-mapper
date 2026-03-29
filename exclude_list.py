# External exclude patterns for directory mapper
# Organized by category similar to LABEL_RULES structure

EXCLUDE_RULES = {
    'File_Extensions': {
        'patterns': [
            # '.angular',
            # '.htm',
            # '.xml',
            # '.tmp',
            # '.venv'
        ]
    },
    'Directories': {
        'patterns': [
            'Kiwix',
            'OEBPS',
            'Movies',
            # 'RECYCLE.BIN'
        ]
    },
    'System_Files': {
        'patterns': [
            '$RECYCLE.BIN',
            # 'System Volume Information',
            'Desktop.ini'
        ]
    }
}
