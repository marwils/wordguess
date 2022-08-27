from collections import defaultdict


class Guesser:
    def __init__(
        self,
        wordlist: list,
        word_length: int,
        excluded_characters: list = ["ä", "ö", "ü", "ß"],
        safe_characters: dict = {},
        characters_anywhere: dict = {},
        characters_excluded_at: dict = {},
    ) -> None:
        self.__wordlist = wordlist
        self.__word_length = word_length
        self.__excluded_characters = excluded_characters
        self.__safe_characters = safe_characters
        self.__characters_anywhere = characters_anywhere
        self.__characters_excluded_at = characters_excluded_at

    def validate(
        self,
        validate_wordlist_not_empty: bool = True,
        validate_word_length: bool = True,
        validate_excluded_characters: bool = True,
        validate_safe_characters: bool = True,
        validate_characters_anywhere: bool = True,
        validate_characters_excluded_at: bool = True,
    ):
        if validate_wordlist_not_empty:
            self.__validate_wordlist_not_empty()

        if validate_word_length:
            self.__validate_word_length()

        if validate_excluded_characters:
            self.__validate_excluded_characters()

        if validate_safe_characters:
            self.__validate_safe_characters()

        if validate_characters_anywhere:
            self.__validate_characters_anywhere()

        if validate_characters_excluded_at:
            self.__validate_characters_excluded_at()

    def __validate_wordlist_not_empty(self):
        if not self.__wordlist:
            raise ValueError("Empty wordlist")

    def __validate_word_length(self):
        for word in self.__wordlist:
            if len(word) != self.__word_length:
                raise ValueError(f'Unexpected length of word in wordlist: "{word}" with length of: {len(word)}')

    def __validate_excluded_characters(self):
        for char in self.__excluded_characters:
            if not char:
                raise ValueError("Missing character in exluded_chars list")

            if len(char) != 1:
                raise ValueError("Only one character per exclusion allowed in exluded_chars list")

    def __validate_safe_characters(self):
        safe_chars = defaultdict(int)
        for char, idx in self.__safe_characters.items():
            if not char:
                raise ValueError("Missing character in safe_characters dict")

            if len(char) != 1:
                raise ValueError("Only one character per safe character allowed in safe_characters dict")

            if idx is None:
                raise ValueError(f'Missing index in safe_characters for character "{char}"')

            if not isinstance(idx, int):
                raise TypeError(f'Type of index is not integer of safe_characters character "{char}"')

            if idx < 0 or idx > self.__word_length - 1:
                raise IndexError(f'Index of safe character "{char}" out of bounds')

            for c, i in safe_chars.items():
                if not c == char and i == idx:
                    raise ValueError(f'Safe character "{char}" index is already reserved by "{c}"')

            safe_chars[char] = idx

    def __validate_characters_anywhere(self):
        for char, occurences in self.__characters_anywhere.items():
            if not char:
                raise ValueError("Missing character in characters_anywhere dict")

            if len(char) != 1:
                raise ValueError("Only one character per anywhere character allowed in characters_anywhere dict")

            if occurences is None:
                raise ValueError(f'No occurences defined in safe_characters for character "{char}"')

            if not isinstance(occurences, int):
                raise TypeError(f'Type of amount of occurences is not integer of safe_characters character "{char}"')

            if occurences < 1:
                raise ValueError(
                    f'Occurences of anywhere character "{char}" have to be at least 1'
                )

            if occurences > self.__word_length:
                raise ValueError(
                    f'Occurences of anywhere character "{char}" cannot exceed the amount of word character count '
                    f'{self.__word_length}'
                )

    def __validate_characters_excluded_at(self):
        for char, idx_list in self.__characters_excluded_at.items():
            if not char:
                raise ValueError("Missing character in characters_excluded_at dict")

            if len(char) != 1:
                raise ValueError("Only one character per exclusion allowed in characters_excluded_at dict")

            if not idx_list:
                raise ValueError(f'Missing list of indices for characters_excluded_at character "{char}"')

            if not isinstance(idx_list, list):
                raise TypeError(
                    f'Type of indices for characters_excluded_at is not list for character "{char}"'
                )

            for idx in idx_list:
                if idx is None:
                    raise ValueError(f'Missing index for characters_excluded_at character "{char}"')

                if not isinstance(idx, int):
                    raise TypeError(f'Type of index for characters_excluded_at is not integer for character "{char}"')

                if idx < 0 or idx > self.__word_length - 1:
                    raise IndexError(f'Index of characters_excluded_at character "{char}" out of bounds')

    def guess(self) -> list:
        wordlist = self.__wordlist
        return wordlist
