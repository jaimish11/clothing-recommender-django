from django import forms

class LoginForm(forms.Form):
	email = forms.EmailField(max_length = 254)
	password = forms.CharField(max_length = 20, widget = forms.PasswordInput)

	def clean(self):
		cleaned_data  = super(LoginForm, self).clean()
		email = cleaned_data.get('email')
		password = cleaned_data.get('password')
		if not email:
			raise forms.ValidationError('Please enter email')
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