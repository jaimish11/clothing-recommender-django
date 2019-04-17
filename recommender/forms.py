from django import forms

class LoginForm(forms.Form):
	username = forms.CharField(help_text = 'Enter username', max_length = 254, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
	password = forms.CharField(help_text = 'Enter password', max_length = 20, widget = forms.PasswordInput(attrs={'placeholder':'Password'}))

	def clean(self):
		cleaned_data  = super(LoginForm, self).clean()
		username = cleaned_data.get('username')
		password = cleaned_data.get('password')
		if not username:
			raise forms.ValidationError('Please enter username')
		elif not password:
			raise forms.ValidationError('Please enter password')

class PreferenceForm(forms.Form):
	FILTER_CHOICES = (
		('item_type', 'Type (e.g jeans, t-shirts)'),
		('color', 'Color'),
		('fit', 'Fit'),
		('occasion', 'Occasion'),
		('pattern', 'Pattern'),
		('fabric', 'Fabric'),
		('length', 'Length'),
	)
	preferences = forms.ChoiceField(choices = FILTER_CHOICES)